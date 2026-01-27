/**
 * ART OF PROOF: SERVICE RECONSTRUCTION DASHBOARD
 * Complete UI for military service record reconstruction
 */

import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock, AlertCircle, FileText, MapPin, Award, Upload } from 'lucide-react';

// This would be imported from your tRPC setup
// import { trpc } from '../utils/trpc';

export default function ServiceReconstruction() {
  // Mock data for demonstration - replace with actual tRPC hooks
  const reconstruction = {
    id: '1',
    completion_percentage: 45,
    categories: [
      {
        id: '1',
        category_name: 'Enlistment Records',
        priority: 'critical',
        total_items: 6,
        completed_items: 4,
        completion_percentage: 67,
        items: []
      },
      {
        id: '2',
        category_name: 'Training Records',
        priority: 'high',
        total_items: 12,
        completed_items: 3,
        completion_percentage: 25,
        items: []
      }
    ],
    dutyStations: [
      {
        id: '1',
        station_name: 'Fort Bragg',
        city: 'Fayetteville',
        state: 'NC',
        start_date: '1990-01-15',
        end_date: '1993-08-20',
        completion_percentage: 55,
        hazardExposures: [
          {
            hazardType: 'noise_exposure',
            hazardName: 'Artillery Range Proximity',
            exposureDays: 1200,
            severity: 'high',
            presumptive: false
          }
        ]
      }
    ],
    deployments: []
  };
  
  const stats = {
    total_documents: 150,
    uploaded_documents: 68,
    missing_documents: 72,
    requested_documents: 10,
    critical_missing: 5,
    duty_stations: 3,
    deployments: 2,
    presumptive_exposures: 3
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-900 to-green-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold mb-4">
            Complete Military Service Reconstruction
          </h1>
          <p className="text-xl text-blue-100 mb-8">
            Building the complete record that wins your VA claim
          </p>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-2">
                <FileText className="w-8 h-8" />
                <span className="text-3xl font-bold">{stats.total_documents}</span>
              </div>
              <div className="text-sm opacity-90">Total Documents</div>
            </div>
            
            <div className="bg-green-500/20 rounded-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-2">
                <CheckCircle className="w-8 h-8" />
                <span className="text-3xl font-bold">{stats.uploaded_documents}</span>
              </div>
              <div className="text-sm opacity-90">Uploaded</div>
            </div>
            
            <div className="bg-red-500/20 rounded-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-2">
                <XCircle className="w-8 h-8" />
                <span className="text-3xl font-bold">{stats.missing_documents}</span>
              </div>
              <div className="text-sm opacity-90">Missing</div>
            </div>
            
            <div className="bg-yellow-500/20 rounded-lg p-6 border border-white/20">
              <div className="flex items-center justify-between mb-2">
                <Clock className="w-8 h-8" />
                <span className="text-3xl font-bold">{stats.requested_documents}</span>
              </div>
              <div className="text-sm opacity-90">Requested</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Overview */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Overall Progress</h2>
            <span className="text-3xl font-bold text-blue-600">
              {reconstruction.completion_percentage}%
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-6 mb-4">
            <div 
              className="bg-gradient-to-r from-blue-600 to-green-600 h-6 rounded-full transition-all duration-1000 flex items-center justify-center text-white text-sm font-medium"
              style={{ width: `${reconstruction.completion_percentage}%` }}
            >
              {reconstruction.completion_percentage > 10 && `${reconstruction.completion_percentage}%`}
            </div>
          </div>
          
          {/* Status Message */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-6">
            <p className="text-blue-900 font-medium">
              📈 Making progress: You're building a strong case. Keep adding documents for maximum impact.
            </p>
          </div>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 text-gray-600 mb-2">
                <MapPin className="w-5 h-5" />
                <span className="text-sm">Duty Stations Documented</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{stats.duty_stations}</div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 text-gray-600 mb-2">
                <Award className="w-5 h-5" />
                <span className="text-sm">Deployments Tracked</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{stats.deployments}</div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 text-gray-600 mb-2">
                <AlertCircle className="w-5 h-5" />
                <span className="text-sm">Presumptive Exposures Found</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{stats.presumptive_exposures}</div>
            </div>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <button className="bg-blue-500 text-white p-6 rounded-lg hover:opacity-90 transition-opacity text-left">
            <div className="flex items-center gap-3 mb-2">
              <Upload className="w-6 h-6" />
              <h3 className="text-lg font-bold">Upload Documents</h3>
            </div>
            <p className="text-sm text-white/90">Add DD214, medical records, or service documents</p>
          </button>
          
          <button className="bg-green-500 text-white p-6 rounded-lg hover:opacity-90 transition-opacity text-left">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="w-6 h-6" />
              <h3 className="text-lg font-bold">Request from NARA</h3>
            </div>
            <p className="text-sm text-white/90">Auto-generate SF-180 form for official records</p>
          </button>
          
          <button className="bg-purple-500 text-white p-6 rounded-lg hover:opacity-90 transition-opacity text-left">
            <div className="flex items-center gap-3 mb-2">
              <MapPin className="w-6 h-6" />
              <h3 className="text-lg font-bold">Add Duty Station</h3>
            </div>
            <p className="text-sm text-white/90">Map hazard exposures for each station</p>
          </button>
        </div>
        
        {/* Checklist Categories */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Document Checklist</h2>
          
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {reconstruction.categories.map(category => (
              <div 
                key={category.id}
                className={`bg-white rounded-lg shadow-md p-6 border-t-4 ${
                  category.priority === 'critical' ? 'border-red-500' :
                  category.priority === 'high' ? 'border-orange-500' :
                  'border-blue-500'
                } cursor-pointer hover:shadow-lg transition-shadow`}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{category.category_name}</h3>
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
                    {category.completed_items}/{category.total_items}
                  </span>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${category.completion_percentage}%` }}
                  />
                </div>
                
                <div className="text-sm text-gray-600">
                  {category.completion_percentage}% Complete
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Duty Stations */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Duty Stations & Hazard Exposure</h2>
          
          <div className="space-y-4">
            {reconstruction.dutyStations.map(station => (
              <div 
                key={station.id}
                className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{station.station_name}</h3>
                    <p className="text-gray-600">{station.city}, {station.state}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(station.start_date).toLocaleDateString()} - {new Date(station.end_date).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                    {station.completion_percentage}% Complete
                  </div>
                </div>
                
                {/* Hazard List */}
                {station.hazardExposures && station.hazardExposures.length > 0 && (
                  <div className="mt-4 pl-4 border-l-2 border-red-300">
                    {station.hazardExposures.map((hazard, idx) => (
                      <div key={idx} className="mb-2">
                        <span className="font-medium text-gray-900">{hazard.hazardName}</span>
                        <span className="text-sm text-gray-600 ml-2">
                          ({hazard.exposureDays} days, {hazard.severity} severity)
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* NARA Request Panel */}
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg shadow-md p-8 border-l-4 border-blue-500">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Missing Critical Records?</h3>
          <p className="text-gray-700 mb-6">
            We can automatically request your Official Military Personnel File (OMPF) from the National Archives.
            This includes service records, unit assignments, awards, and more.
          </p>
          
          <div className="bg-white rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-gray-900 mb-2">What you'll get:</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>✓ Complete service history</li>
              <li>✓ All duty station orders</li>
              <li>✓ Performance evaluations</li>
              <li>✓ Training records</li>
              <li>✓ Award citations</li>
            </ul>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium">
              Generate SF-180 Request Form
            </button>
            <span className="text-sm text-gray-600">
              Typical response time: 90-120 days
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
